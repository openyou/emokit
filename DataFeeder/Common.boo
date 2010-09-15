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
	IKey = (0x31, 0x00, 0x35, 0x54, 0x38, 0x10, 0x37, 0x42, 0x31, 0x00, 0x35, 0x48, 0x38, 0x00, 0x37, 0x50)
	Key as (byte)
	static I = 0
	def NextPacket() as (byte):
		if Packet == null:
			Temp = array(byte, 32)
			Packet = array(byte, 33)
			Key = array(byte, 16)
			for i in range(16):
				Key[i] = IKey[i]
		
		Temp[0] = Counter
		Counter += 1
		if Counter == 128:
			Counter = 0xE9
		elif Counter == 0xEA:
			Counter = 0
		
		Array.Copy(Data[I], 0, Temp, 1, 31)
		I = (I + 1) % Data.Length
		
		rijn = RijndaelManaged()
		rijn.Mode = CipherMode.ECB
		crypt = rijn.CreateEncryptor(Key, array(byte, 0))
		crypt.TransformBlock(Temp, 0, 16, Packet, 0)
		crypt = rijn.CreateEncryptor(Key, array(byte, 0))
		crypt.TransformBlock(Temp, 16, 16, Packet, 16)
		Array.Copy(Temp, 0, Packet, 1, 32)
		return Packet
