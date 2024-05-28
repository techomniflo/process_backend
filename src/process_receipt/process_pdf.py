from typing import Optional, Tuple , Union
import httpx
import asyncio
import logging

from src.utils import ist_datetime_current
from src.db import DB
from src.s3 import upload_to_s3

logging.basicConfig(level=logging.INFO)  # Set the logging level
logger = logging.getLogger(__name__)


async def process_receipt(id:int,file_content:bytes) -> Union[Tuple[int, str], Tuple[bool, bool] , Tuple[int,None]]:
    """
    Process a receipt file asynchronously.

    Args:
        id (int): The ID of the SoftUpload Table.
        file_content (bytes): The content of the receipt file.

    Returns:
        Union[Tuple[int, str], Tuple[bool, bool], Tuple[int, None]]: A tuple containing processed information or status.
    """

    current_time=ist_datetime_current()

    # Initial values for database insertion
    iv={"creation":current_time,"modified":current_time,"softupload_id":id,"image_link":None,"image_path":None,'is_processed':0,"processed_text":None}
    
    async def convert_to_image():
        """
        Convert XPS file to PNG image and upload to S3.
        """
        async with httpx.AsyncClient() as client:
            url="https://converter.beaglenetwork.com/pdf2png"
            response= await client.post(url, files={"file": file_content},timeout=20.0)
            if response.status_code == 200:
                filename=f"{id}.png"
                image_path="processed_images/"+filename
                image_link='https://beaglebucket.s3.amazonaws.com/'+image_path
                # Upload to S3
                upload_to_s3(response.content,image_path)
                iv["image_link"]=image_link
                iv["image_path"]=image_path

    async def extract_text():
        """
        Extract text from XPS file.
        """
        async with httpx.AsyncClient() as client:
            url="https://converter.beaglenetwork.com/pdf2txt"
            response =await client.post(url, files={"file": (f"{id}.pdf",file_content)},timeout=20.0)
            if response.status_code == 200:
                if len(response.text)>10:
                    iv['processed_text']=response.text
                    iv['is_processed']=1
    
    try:
        result = await asyncio.gather(convert_to_image(),extract_text(),return_exceptions=False)
    except httpx.TimeoutException as exc:
        logger.error("Request timed out: %s", exc)
    except httpx.HTTPStatusError as exc:
        logger.error("HTTP error: %s, Response: %s", exc, exc.response)
    except httpx.RequestError as exc:
        logger.error("Request error: %s", exc)
    
    # If either image link or processed text is available, insert into the database
    if iv["image_link"] or iv["processed_text"]:
        async with DB.transaction():
            id=await DB.execute("INSERT INTO ProcessedReceipt (creation,modified,softupload_id,image_link,image_path,is_processed,processed_text) VALUES (:creation,:modified,:softupload_id,:image_link,:image_path,:is_processed,:processed_text)", values=iv)

    if iv["processed_text"]:
         return (id,iv["processed_text"])
    
    return (False,False)