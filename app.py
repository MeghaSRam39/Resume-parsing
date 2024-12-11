# import streamlit as st
# import pandas as pd
# import base64, random
# import time, datetime
# import io, random
# from streamlit_tags import st_tags
# from PIL import Image
# import pymysql 
import os
# import pafy
# import plotly.express as px 
# import nltk
from dotenv import load_dotenv

load_dotenv('.env')


password = os.getenv('password')
print(password)

# nltk.download('stopwords')

# def fetch_yt_video(link):
#     video = pafy.new(link)
#     return video.title


#connect to mysql db
connection = pymysql.connect(host = 'localhost', user = 'root', password = password, db = 'cv')
cursor = connection.cursor()

