
import logging
import struct
import subprocess
import time
from typing import IO, BinaryIO, Optional
import warnings

from .exception import UndefinedHeader

logger = logging.getLogger(__name__)

class BveReplayer:

    __to_int: struct.Struct = struct.Struct('i')
    __to_unsigned_char: struct.Struct = struct.Struct('B')
    __to_float: struct.Struct = struct.Struct('f')
    __to_double: struct.Struct = struct.Struct('d')

    last_elapse_time: Optional[int] = None

    def __init__(self, script_path:str, record_path:str) -> None:
        self.proc = subprocess.Popen(["python", script_path, "--no-rec"], stdin=subprocess.PIPE, stdout=sys.stdout, bufsize=0)

        if self.proc.stdin is None:
            raise ValueError("Could not open stdin")

        with open(record_path, "rb") as f:
            while True:
                try:
                    header:bytes = f.read(1)
                    self.proc.stdin.write(header)
                    match header:
                        case b'':
                            break
                        case b'\x00':
                            self.__read_unsigned_char(f, self.proc.stdin)
                            self.__read_unsigned_char(f, self.proc.stdin)
                            self.__read_unsigned_char(f, self.proc.stdin)
                        case b'\x01':
                            break
                        case b'\x10':
                            self.__read_int(f, self.proc.stdin)
                            self.__read_int(f, self.proc.stdin)
                            self.__read_int(f, self.proc.stdin)
                            self.__read_int(f, self.proc.stdin)
                            self.__read_int(f, self.proc.stdin)
                        case b'\x20':
                            self.__read_int(f, self.proc.stdin)
                        case b'\x30':
                            self.__read_double(f, self.proc.stdin)
                            self.__read_float(f, self.proc.stdin)
                            current_time = self.__read_int(f, self.proc.stdin)
                            if self.last_elapse_time:
                                wait_time = (current_time - self.last_elapse_time)/1000
                                if 0 < wait_time < 1:
                                    time.sleep(wait_time)
                            self.last_elapse_time = current_time
                            self.__read_float(f, self.proc.stdin)
                            self.__read_float(f, self.proc.stdin)
                            self.__read_float(f, self.proc.stdin)
                            self.__read_float(f, self.proc.stdin)
                            self.__read_float(f, self.proc.stdin)
                            self.__read_float(f, self.proc.stdin)
                        case b'\x40':
                            self.__read_int(f, self.proc.stdin)
                        case b'\x41':
                            self.__read_int(f, self.proc.stdin)
                        case b'\x42':
                            self.__read_int(f, self.proc.stdin)
                        case b'\x50':
                            self.__read_int(f, self.proc.stdin)
                        case b'\x51':
                            self.__read_int(f, self.proc.stdin)
                        case b'\x60':
                            self.__read_int(f, self.proc.stdin)
                        case b'\x61':
                            self.__read_int(f, self.proc.stdin)
                        case b'\x70':
                            pass
                        case b'\x71':
                            pass
                        case b'\x80':
                            self.__read_int(f, self.proc.stdin)
                        case b'\x90':
                            self.__read_int(f, self.proc.stdin)
                            self.__read_int(f, self.proc.stdin)
                            self.__read_float(f, self.proc.stdin)
                            self.__read_int(f, self.proc.stdin)
                        case b'\xA0':
                            self.__read_unsigned_char(f, self.proc.stdin)
                            self.__read_int(f, self.proc.stdin)
                        case b'\xA1':
                            self.__read_unsigned_char(f, self.proc.stdin)
                            self.__read_int(f, self.proc.stdin)
                        case _:
                            raise UndefinedHeader(header)
                except UndefinedHeader:
                    logger.exception("", exc_info=True)
                    sys.exit(1)
            while byte := f.read(1):
                self.proc.stdin.write(byte)

        self.proc.terminate()

    def __read_bytes(self, size:int, input_:BinaryIO, output:IO[bytes]) -> bytes:
        binary = input_.read(size)
        output.write(binary)
        return binary

    def __read_int(self, input_:BinaryIO, output:IO[bytes]) -> int:
        return self.__to_int.unpack(self.__read_bytes(4, input_, output))[0]

    def __read_unsigned_char(self, input_:BinaryIO, output:IO[bytes]) -> int:
        return self.__to_unsigned_char.unpack(self.__read_bytes(1, input_, output))[0]

    def __read_float(self, input_:BinaryIO, output:IO[bytes]) -> float:
        return self.__to_float.unpack(self.__read_bytes(4, input_, output))[0]

    def __read_double(self, input_:BinaryIO, output:IO[bytes]) -> float:
        return self.__to_double.unpack(self.__read_bytes(8, input_, output))[0]

if __name__ == "__main__":
    import sys

    try:
        script_path = sys.argv[1]
        record_path = sys.argv[2]
    except IndexError:
        raise ValueError("Lack of arguments")

    if script_path[-3:] != ".py":
        warnings.warn("Script path may be incorrect. Would you like to continue? [y/n]", RuntimeWarning)
        match input():
            case "y":
                pass
            case "n":
                sys.exit(-1)
            case _:
                warnings.warn("Invalid input", RuntimeWarning)
                sys.exit(-1)

    BveReplayer(script_path, record_path)

    input("Press Enter to exit...")
