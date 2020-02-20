import struct

CHUNK = 1024 * 1024 * 100 #process 100 megs at a time.

TOPLEVEL = ['icpf']

LAST_POSITION = 0

def look(data):
    for tl in TOPLEVEL:
        if tl in data:
            print "LOOK:",tl
            yield tl

def extract(f,tag,position, chunk_table_f, stsz_table_f, end):
    global LAST_POSITION

    if LAST_POSITION != 0:
        # rewrite last size
        print("rewriting last position %d", position - LAST_POSITION)
        stsz_table_f.seek(-4, 1)
        stsz_table_f.write(struct.pack(">I", position - LAST_POSITION))
    LAST_POSITION = position
    loc = f.tell()
    f.seek(position)
    dat = f.read(4)
    assert tag == f.read(4)
    found, size = validate(f, position)
    if found:
        data = struct.pack(">Q", position)
        chunk_table_f.write(data)
        data = struct.pack(">I", size)
        stsz_table_f.write(data)
        return True
    else:
        f.seek(loc)
        return False

def validate(f, position):
    f.seek(position, 0)
    current_start = f.tell()

    dat = f.read(8)
    already_seeked = 8
    if dat:
        size, tag = struct.unpack(">I4s",dat)
        print "    EXTRACT:",tag+"@%d-%d-%d"%(current_start,size,current_start+size)
        f.seek(size-already_seeked,1)
    else:
        print "    no dat"
        return (False, -1)

    current_start = f.tell()
    dat = f.read(8)
    already_seeked = 8
    if dat:
        admd_size, tag2 = struct.unpack(">I4s",dat)
        if tag2 == "admd":
            full_size = size + admd_size
            f.seek(admd_size-already_seeked,1)
            print "    EXTRACT:",tag2+"@%d-%d-%d-%d"%(current_start,admd_size,current_start+admd_size, full_size)
            return (True, size + admd_size)
        else:
            print "   seeking back to %d"%(current_start)
            f.seek(current_start, 0)
            # quick validation of size
            if size < 9000000 and size > 10000:
                print "    no admd found, returning just icpf"
                return (True, size)
            else:
                print "    size of icpf is bad"
                return (False, -1)

    else:
        print "no dat"
        return (False, -1)

def process_data(f, start = 0, end = 0, chunk_table_f = None, stsz_table_f = None):
    #hack to correctly account for file position since we always keep 8 bytes in the buffer
    buffer = "00000000" 
    #Keep tract of the file position relative to the beginning of the buffer
    POS = start-CHUNK
    # store any chucks that we find.
    found = {}
    f.seek(start, 0)
    while 1 or POS < end:
        read_chunk = CHUNK
        if POS + read_chunk >= end:
             read_chunk = end - POS
        buffer += f.read(read_chunk)
        if len(buffer) == 8:
            break
        POS += read_chunk
        for tag in look(buffer):
            pos = POS + buffer.index(tag) - 4 - 8
            if extract(f, tag, pos, chunk_table_f, stsz_table_f, end):
                POS = f.tell() -read_chunk
                break
        buffer = buffer[-8:]

    chunk_table_f.flush()
    f.seek(0, 2)
    print "END: %d"%(f.tell())
    f.close()
    chunk_table_f.close()
    stsz_table_f.close()
    return found

if __name__=='__main__':
    import sys
    if len(sys.argv) == 2:
        disk = open(sys.argv[1],'rb')
        process_data(disk)
    elif len(sys.argv) == 3:
        disk = open(sys.argv[1],'rb')
        process_data(disk, start=int(sys.argv[2]))
    elif len(sys.argv) == 5:
        disk = open(sys.argv[1],'rb')
        chunk_table_fn = sys.argv[4]+".co64"
        stsz_fn = sys.argv[4]+".stsz"
        chunk_table_f = open(chunk_table_fn,'wb+')
        stsz_table_f = open(stsz_fn,'wb+')
        process_data(disk, start=int(sys.argv[2]), end=int(sys.argv[3]), chunk_table_f=chunk_table_f, stsz_table_f=stsz_table_f)
    else:
        print "Usage: python recover.py /path/to/disk.dat"

