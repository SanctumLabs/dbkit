"""
File format will contain file header and body
"""
from typing import BinaryIO
from dataclasses import dataclass
import struct
import array

MAGIC_NUMBER: bytes = b"MAZE"


@dataclass(frozen=True)
class FileHeader:
    """
    Defines the file header of the file.
    """

    format_version: int
    width: int
    height: int

    def write(self, file: BinaryIO) -> None:
        """writes content into a supplied binary file"""
        file.write(MAGIC_NUMBER)
        # B stands for unsigned byte, which works with the expected version field
        file.write(struct.pack("B", self.format_version))
        # The less than symbol (<) indicates a little-endian byte order. The number that follows communicates how many
        # consecutive values of the same type you’re going to provide. Finally, the uppercase letter 'I' denotes a
        # 32-bit unsigned integer type.
        #
        # So, the string <2I means two unsigned integers, one after the other, in little-endian order. It makes sense
        # to group as many fields together as possible to limit the number of expensive system calls that write a block
        # of data to the file.
        file.write(struct.pack("<2I", self.width, self.height))

    @classmethod
    def read(cls, file: BinaryIO) -> "FileHeader":
        """reads contents from a supplied file to create a file header"""
        assert file.read(len(MAGIC_NUMBER)) == MAGIC_NUMBER, "Unknown file type"
        # struct.unpack() always returns a tuple, hence the need to add a comma(,).
        (format_version,) = struct.unpack("B", file.read(1))
        width, height = struct.unpack("<2I", file.read(2 * 4))
        return cls(format_version=format_version, width=width, height=height)


@dataclass(frozen=True)
class FileBody:
    """
    File body
    """

    square_values: array.array

    @classmethod
    def read(cls, header: FileHeader, file: BinaryIO) -> "FileBody":
        """
        Factory method to create a file body given the header and the file.
        The 'B' typecode ensures that the correct underlying C type is used. This will be an array of unsigned bytes.
        This reads the header before so that the internal file pointer is set at the right offset. The information
        stored in the file header is used to calculate the number of remaining bytes to read by multiplying the width
        and height of the maze. This data is then converted to a byte array and passed to the FileBody instance
        """
        return cls(array.array("B", file.read(header.width * header.height)))

    def write(self, file: BinaryIO) -> None:
        """
        Writes the file body to a file
        """
        # .tybytes() takes care of serializing the items into the correct data type in the requested byte order
        file.write(self.square_values.tobytes())
