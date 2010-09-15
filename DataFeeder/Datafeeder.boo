namespace Datafeeder

import EasyHook
import System.Collections.Generic
import System.Diagnostics
import System.IO
import System.Runtime.Remoting

class Datafeeder:
	def constructor(datafn as string):
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
			edata = array(byte, 31)
			for i in range(31):
				edata[i] = int.Parse(elems[i], System.Globalization.NumberStyles.AllowHexSpecifier)
			data.Add(edata)
		
		DatafeederInterface.Data = data.ToArray()
		
		channelName as string
		RemoteHooking.IpcCreateServer [of DatafeederInterface](channelName, WellKnownObjectMode.SingleCall)
		pid as int
		RemoteHooking.CreateAndInject(
				'C:\\Program Files (x86)\\EPOC Control Panel\\EmotivControlPanel.exe', 
				'', 
				'Datafeeder.Inject.dll', 
				'Datafeeder.Inject.dll', 
				pid, 
				channelName
			)
		
		try:
			Process.GetProcessById(pid).WaitForExit()
		except:
			return

Datafeeder(argv[0])

