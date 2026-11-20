import argparse,uvicorn
from .config import settings
def main():
    parser=argparse.ArgumentParser(prog="usb-operator"); parser.add_argument("command",choices=["serve"],nargs="?",default="serve"); parser.add_argument("--host",default=settings.host); parser.add_argument("--port",type=int,default=settings.port); args=parser.parse_args(); uvicorn.run("usb_operator.api.app:app",host=args.host,port=args.port,reload=False)
if __name__=="__main__": main()
