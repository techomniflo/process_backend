from typing import List,AsyncGenerator
import pytz
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import Integer,String,DateTime,Text,Float,Date
from sqlalchemy.orm import Mapped,Session
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession,async_sessionmaker

from src import MYSQL_STRING

mysql_string=MYSQL_STRING

engine = create_async_engine(mysql_string)

SessionLocal = async_sessionmaker(
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

class Base(DeclarativeBase):
    pass


class SoftUpload(Base):
    __tablename__ = 'SoftUpload'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    creation = mapped_column(DateTime(timezone=True), default=datetime.now(pytz.timezone('Asia/Kolkata')))
    ip = mapped_column(String(100))
    content_type = mapped_column(String(255))
    unique_id = mapped_column(String(100))
    release_version = mapped_column(String(100))
    file_path = mapped_column(String(100))
    file_extension = mapped_column(String(10))
    file_link = mapped_column(String(100))

    # processed_receipts = relationship('ProcessedReceipt', order_by='ProcessedReceipt.id', back_populates='softupload')
    # tag_soft_uploads = relationship('TagSoftUpload', order_by='TagSoftUpload.id', back_populates='softupload')


class ProcessedReceipt(Base):
    __tablename__ = 'ProcessedReceipt'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    creation = mapped_column(DateTime(timezone=True), default=datetime.now(pytz.timezone('Asia/Kolkata')))
    modified = mapped_column(DateTime(timezone=True), onupdate=datetime.now(pytz.timezone('Asia/Kolkata')))
    softupload_id = mapped_column(Integer, ForeignKey('SoftUpload.id',ondelete='SET NULL'))
    is_processed = mapped_column(String(1))
    image_link = mapped_column(String(255))
    image_path = mapped_column(String(255))
    processed_text = mapped_column(Text)
    processed_json = mapped_column(Text)

    # softupload = relationship('SoftUpload', back_populates='processed_receipts')



class TagSoftUpload(Base):
    __tablename__ = 'TagSoftUpload'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    creation = mapped_column(DateTime(timezone=True), default=datetime.now(pytz.timezone('Asia/Kolkata')))
    softupload_id = mapped_column(Integer, ForeignKey('SoftUpload.id'))
    type = mapped_column(String(50), nullable=False)
    sub_type = mapped_column(String(50))

    # softupload = relationship('SoftUpload', back_populates='tag_soft_uploads')


class ParsedItem(Base):
    __tablename__ = 'ParsedItem'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    creation = mapped_column(DateTime(timezone=True), default=datetime.now(pytz.timezone('Asia/Kolkata')))
    processed_receipt_id = mapped_column(Integer, ForeignKey('ProcessedReceipt.id',ondelete='SET NULL'), nullable=True)
    observed_name = mapped_column(String(500))
    guessed_full_name = mapped_column(String(500))
    qty = mapped_column(Float)
    uom = mapped_column(String(50))
    mrp = mapped_column(Float)
    price = mapped_column(Float)
    total_amount = mapped_column(Float)
    barcode = mapped_column(String(255), default=None)
    date = mapped_column(String(50))
    time = mapped_column(String(50))
    store_name = mapped_column(String(255))
    store_address = mapped_column(String(255))
    bill_id = mapped_column(String(255))
    gstin = mapped_column(String(20))
    total_qty = mapped_column(Float)
    total_items = mapped_column(Float)
    final_amount = mapped_column(Float)
    store_cashier = mapped_column(String(255))
    store_phone_no = mapped_column(String(100))
    store_email = mapped_column(String(255))
    customer_phone_number = mapped_column(String(100))
    mode_of_payment = mapped_column(String(500))
    customer_name = mapped_column(String(500))
    customer_details = mapped_column(String(500))

    # processed_receipt = relationship('ProcessedReceipt', back_populates='parsed_items')


class StoreProfile(Base):
    __tablename__ = 'StoreProfile'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    creation = mapped_column(DateTime(timezone=True), default=datetime.now(pytz.timezone('Asia/Kolkata')))
    store_name = mapped_column(String(255), nullable=False)
    store_owner_name = mapped_column(String(255), nullable=False)
    store_owner_contact_no = mapped_column(String(50), nullable=False)
    store_landline_no = mapped_column(String(50))
    address = mapped_column(Text, nullable=False)
    locality = mapped_column(String(255))
    city = mapped_column(String(50), nullable=False)
    state = mapped_column(String(50), nullable=False)
    zipcode = mapped_column(String(50), nullable=False)
    latitude = mapped_column(String(100), nullable=False)
    longitude = mapped_column(String(100), nullable=False)
    average_monthly_transaction = mapped_column(Integer)
    average_monthly_turnover = mapped_column(Integer)
    average_basket_sale_value = mapped_column(Integer)
    store_format = mapped_column(String(10), nullable=False)
    self_service = mapped_column(String(1), nullable=False)
    presence_of_shopping_cart = mapped_column(String(1), nullable=False)
    presence_of_shopping_basket = mapped_column(String(1), nullable=False)
    store_profile = mapped_column(String(1), nullable=False)
    no_of_tills = mapped_column(Integer)
    business_hours = mapped_column(String(100))
    area_of_sqft = mapped_column(Integer, nullable=False)
    average_footfall = mapped_column(Integer, nullable=False)
    trade_profile_of_store = mapped_column(String(50))
    retail_percentage = mapped_column(Integer)
    presence_of_electronic_weighting_machine = mapped_column(String(1))
    presence_of_visi_cooler = mapped_column(String(1))
    presence_of_other_cooler = mapped_column(String(1))
    presence_of_freezer = mapped_column(String(1))
    air_cooling = mapped_column(String(1))
    pos_installation_date = mapped_column(Date)
    pos_make = mapped_column(String(100))
    pos_model = mapped_column(String(100))
    years_of_origin = mapped_column(Integer)

class FMCG_Master(Base):
    __tablename__ = 'FMCG_Master'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(500))
    brand = mapped_column(String(50))
    manufacturer = mapped_column(String(50))
    mrp = mapped_column(Float)
    price = mapped_column(Float)
    discount_value = mapped_column(Float)
    discount_percentage = mapped_column(Float)
    category_lvl_1 = mapped_column(String(50))
    category_lvl_2 = mapped_column(String(50))
    category_lvl_3 = mapped_column(String(50))
    category_lvl_4 = mapped_column(String(50))

class JioMart(Base):
    __tablename__ = 'JioMart'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    creation = mapped_column(DateTime(timezone=True), default=datetime.now(pytz.timezone('Asia/Kolkata')))
    modified = mapped_column(DateTime(timezone=True), onupdate=datetime.now(pytz.timezone('Asia/Kolkata')))
    product_code = mapped_column(String(100))
    name = mapped_column(String(500))
    brand = mapped_column(String(255))
    manufacturer = mapped_column(String(255))
    mrp = mapped_column(Float)
    price = mapped_column(Float)
    discount_value = mapped_column(Float)
    discount_percentage = mapped_column(Float)
    category_lvl_1 = mapped_column(String(255))
    category_lvl_2 = mapped_column(String(255))
    category_lvl_3 = mapped_column(String(255))
    category_lvl_4 = mapped_column(String(255))

class BigBasket(Base):
    __tablename__ = 'bigbasket'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    creation = mapped_column(DateTime(timezone=True), default=datetime.now(pytz.timezone('Asia/Kolkata')))
    modified = mapped_column(DateTime(timezone=True), onupdate=datetime.now(pytz.timezone('Asia/Kolkata')))
    name = mapped_column(String(500))
    brand = mapped_column(String(255))
    mrp = mapped_column(Float)
    price = mapped_column(Float)
    ean_code = mapped_column(String(255))
    fssai_number = mapped_column(String(255))
    category_lvl_1 = mapped_column(String(255))
    category_lvl_2 = mapped_column(String(255))
    category_lvl_3 = mapped_column(String(255))

class MatchedItem(Base):
    __tablename__ = 'MatchedItem'

    parsed_item_id = mapped_column(Integer, ForeignKey('ParsedItem.id'), primary_key=True)
    creation = mapped_column(DateTime(timezone=True), default=datetime.now(pytz.timezone('Asia/Kolkata')))
    jiomart_id = mapped_column(Integer, ForeignKey('JioMart.id',ondelete='SET NULL'), nullable=True)
    jiomart_matched = mapped_column(String(1))
    bigbasket_id = mapped_column(Integer, ForeignKey('bigbasket.id',ondelete='SET NULL'), nullable=True)
    bigbasket_matched = mapped_column(String(1))

    # parsed_item = relationship('ParsedItem')
    # jiomart = relationship('JioMart')
    # bigbasket = relationship('BigBasket')

