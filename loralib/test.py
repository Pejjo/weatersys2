import rfm
import time

rfm.init()

while True:
  rxb,rxt=rfm.poll()
  if rxb>0:
     print(rxt," (",rxb," byte)")
#  else:
#     print(".")
  time.sleep(1)

