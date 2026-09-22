# control: crash
import sys
sys.stdout.buffer.write(b'program 441\n')
sys.stdout.buffer.write('\u25f9'.encode('utf-8')[:2])
sys.stdout.buffer.flush()
