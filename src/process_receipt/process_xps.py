from typing import Dict ,Any
import httpx
import asyncio
import logging

from src.utils import ist_datetime_current
from src.s3 import upload_to_azure

logging.basicConfig(level=logging.INFO)  # Set the logging level
logger = logging.getLogger(__name__)


async def process_receipt(id:int,file_content:bytes) -> Dict[str, Any]:
    """
    Processes a receipt by converting an XPS file to a PNG image and extracting text from it.
    
    Args:
        id (int): The ID of the receipt to process.
        file_content (bytes): The content of the XPS file to process.
    
    Returns:
        Dict[str, Any]: A dictionary containing metadata about the processing,
                        including creation and modification times, image link,
                        image path, whether the text was processed, and the processed text.
    """

    current_time=ist_datetime_current()

    # Initial values for database insertion
    iv={"creation":current_time,"modified":current_time,"softupload_id":id,"image_link":None,"image_path":None,'is_processed':0,"processed_text":None}
    
    async def convert_to_image():
        """
        Convert XPS file to PNG image and upload to S3.
        """
        async with httpx.AsyncClient() as client:
            url="https://converter.beaglenetwork.com/xps2png"
            response= await client.post(url, files={"file": file_content},timeout=20.0)
            if response.status_code == 200:
                filename=f"{id}.png"
                image_path="processed_images/"+filename
                # Upload to Azure Blob Storage
                image_link=upload_to_azure(response.content,image_path)
                iv["image_link"]=image_link
                iv["image_path"]=image_path

    async def extract_text():
        """
        Extract text from XPS file.
        """
        async with httpx.AsyncClient() as client:
            url="https://converter.beaglenetwork.com/xps2txt"
            response =await client.post(url, files={"file": (f"{id}.xps",file_content)},timeout=20.0)
            if response.status_code == 200:
                if len(response.text)>10:
                    text_from_xps=response.text
                    iv['processed_text']=text_from_xps
                    iv['is_processed']=1
    
    try:
        result = await asyncio.gather(convert_to_image(),extract_text(),return_exceptions=False)
    except httpx.TimeoutException as exc:
        logger.error("Request timed out: %s", exc)
    except httpx.HTTPStatusError as exc:
        logger.error("HTTP error: %s, Response: %s", exc, exc.response)
    except httpx.RequestError as exc:
        logger.error("Request error: %s", exc)
    
    return iv
