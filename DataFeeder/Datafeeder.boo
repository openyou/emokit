namespace Datafeeder

import EasyHook
import System.Collections.Generic
import System.Diagnostics
import System.IO
import System.Runtime.Remoting

class Datafeeder:
	def constructor(exec as string, datafn as string, type as string):
		Config.Register(
				'Feeds data into Emotiv software', 
				'Datafeeder.exe', 
				'Datafeeder.Inject.dll', 
				'Datafeeder.Common.dll'
			)
		
		data = List [of (byte)]()
		sr = StreamReader(datafn)
		while true:
			line = sr.ReadLine()
			if line == null:
				break
			elems = line.Split(char(' '))
			edata = array(byte, 32)
			for i in range(32):
				edata[i] = int.Parse(elems[i], System.Globalization.NumberStyles.AllowHexSpecifier)
			data.Add(edata)
		
		if type == 'dev':
			key = (0x31, 0x00, 0x39, 0x54, 0x38, 0x10, 0x37, 0x42, 0x31, 0x00, 0x39, 0x48, 0x38, 0x00, 0x37, 0x50)
		else:
			key = (0x31, 0x00, 0x35, 0x54, 0x38, 0x10, 0x37, 0x42, 0x31, 0x00, 0x35, 0x48, 0x38, 0x00, 0x37, 0x50)
		for i in range(16):
			DatafeederInterface.Key[i] = key[i]
		DatafeederInterface.Data = data.ToArray()
		
		channelName as string
		RemoteHooking.IpcCreateServer [of DatafeederInterface](channelName, WellKnownObjectMode.SingleCall)
		#pid as int
		#RemoteHooking.CreateAndInject(
		#		'c:\\python26\\python.exe', 
		#		'c:\\python26\\python.exe C:\\AAA\\Projects\\RawEEG\\emotiv.py', 
		#		'Datafeeder.Inject.dll', 
		#		'Datafeeder.Inject.dll', 
		#		pid, 
		#		channelName
		#	)
		process as Process
		for proc in Process.GetProcesses():
			if 'python' in proc.ProcessName.ToLower():
				process = proc
		RemoteHooking.Inject(
				process.Id, 
				'Datafeeder.Inject.dll', 
				'Datafeeder.Inject.dll', 
				channelName
			)
		
		try:
			Process.GetProcessById(process.Id).WaitForExit()
		except:
			return

if argv.Length > 2:
	Datafeeder(argv[0], argv[1], argv[2])
else:
	Datafeeder(argv[0], argv[1], 'consumer')
