import zipfile
import struct

z = zipfile.ZipFile('2026-09-07-tencer-minaev-audit.zip', 'r')
print('Names:', z.namelist())
print('File size:', z.fp.seek(0, 2))
z.fp.seek(-22, 2)
raw = z.fp.read(22)
print('EOCD raw:', raw.hex())
comment_len = struct.unpack('<H', raw[-22:-20])[0] if len(raw) >= 22 else 0
print('Comment length:', comment_len)