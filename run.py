"""启动服务器。"""

import argparse

import uvicorn

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="启动业余无线电 A 类题库练习系统")
    parser.add_argument("--host", default="0.0.0.0", help="主机地址（默认：0.0.0.0）")
    parser.add_argument("--port", type=int, default=8000, help="端口号（默认：8000）")
    args = parser.parse_args()

    uvicorn.run("api.app:app", host=args.host, port=args.port, reload=True)
