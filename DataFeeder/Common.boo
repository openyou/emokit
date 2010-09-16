namespace Datafeeder

import System
import System.Security.Cryptography

public class DatafeederInterface(MarshalByRefObject):
	def Log(message as string):
		print 'Log:', message
	
	public static Data as ((byte))
	Temp as (byte)
	Packet as (byte)
	Counter as int = 0
	public static Key = array(byte, 16)
	static I = 0
	def NextPacket() as (byte):
		if Packet == null:
			Temp = array(byte, 32)
			Packet = array(byte, 33)
		
		Array.Copy(Data[I], 0, Temp, 0, 32)
		I = (I + 1) % Data.Length
		
		Temp[0] = Counter
		Counter += 1
		if Counter == 128:
			Counter = 0xF1
		elif Counter == 0xF2:
			Counter = 0
		
		rijn = RijndaelManaged()
		rijn.Mode = CipherMode.ECB
		crypt = rijn.CreateEncryptor(Key, array(byte, 0))
		crypt.TransformBlock(Temp, 0, 16, Packet, 0)
		crypt = rijn.CreateEncryptor(Key, array(byte, 0))
		crypt.TransformBlock(Temp, 16, 16, Packet, 16)
		Array.Copy(Temp, 0, Packet, 1, 32)
		return Packet
