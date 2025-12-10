
import os

class Telegram():
  API_ID = int(os.getenv("API_ID", ""))                                   #For hardcoded verision, add your API ID in-between "", same goes to all variables
  API_HASH = os.getenv("API_HASH", "")
  BOT_TOKEN = os.getenv("BOT_TOKEN", "")
  BOT_NICKNAME = os.getenv("BOT_NICKNAME", "")
  
  ADMIN = int(os.getenv("ADMIN", ""))     


  #Foece Sub
  Fusb_name =  os.getenv("Fusb_name", "@botio_devs")                     #Fusb channel user name with @
  Fsub_ID =  int(os.getenv("Fsub_ID", "-1002054575318"))     
  Fsub_Link = os.getenv("Fsub_Link", "https://t.me/+9Mxv8UvcoPw0MjA9")   #Custom Invite Link to track User Joining

  #LOGGING
  SEND_JOIN_LOG = True
  LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "-1002054575318"))
  JOIN_LOG_CHANNEL = ERROR_LOGGER_ID = CHANNEL_ID = LOG_CHANNEL_ID
  
  CHECKER_LOG_TOPIC = 3
  ERROR_LOGGER_TOPIC = 38

  
  #Button Link
  UPDATES_CHANNEL = "https://t.me/botio_devs"
  SUPPORT_CHANNEL = "https://t.me/botio_devs_discuss" 
  

class Db():
  MONGO_URI = os.getenv("MONGO_URI", "your mongo uri") 
  DB_NAME = "ecom-tracker"

  
class Server():
  PORT = 8080
  IS_SERVER = os.getenv("IS_SERVER", False)
