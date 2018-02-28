from os.path import abspath
from aardvark_api.runner import Runner

def main():
    runner = Runner(
        host="localhost",
        port="4567",
        db_path="aardvark.sqlite3",
        package_path=abspath("packages"))
    runner.run()
