namespace Datafeeder

import EasyHook
#import Microsoft.Win32.SafeHandles
import System
import System.Collections
import System.Collections.Generic
import System.IO
import System.Runtime.InteropServices
import System.Runtime.Remoting.Channels
import System.Runtime.Remoting.Channels.Ipc
import System.Threading

class Inject(EasyHook.IEntryPoint):
	public static App as DatafeederInterface
	static Handles = List [of IntPtr]()
	static RPipe as IntPtr
	
	def constructor(context as RemoteHooking.IContext, channel as string):
		App = RemoteHooking.IpcConnectClient [of DatafeederInterface](channel)
		
		properties = Hashtable()
		properties.Add('name', 'client')
		properties.Add('portName', 'client')
		properties.Add('typeFilterLevel', 'Full')
		channel_ = IpcChannel(
				properties,
				System.Runtime.Remoting.Channels.BinaryClientFormatterSinkProvider(properties, null), 
				System.Runtime.Remoting.Channels.BinaryServerFormatterSinkProvider(properties, null)
			)
		ChannelServices.RegisterChannel(channel_, false)
	
	[DllImport('Kernel32.dll', CallingConvention: CallingConvention.StdCall)]
	static def CreatePipe(ref read as IntPtr, ref write as IntPtr, attr as IntPtr, size as int) as bool:
		pass
	
	[DllImport('Kernel32.dll', CallingConvention: CallingConvention.StdCall, CharSet: CharSet.Ansi)]
	static def CreateFileA(fn as string, access as uint, share as uint, secattr as IntPtr, disp as uint, flags as uint, tpl as IntPtr) as IntPtr:
		pass
	[UnmanagedFunctionPointer(CallingConvention.StdCall)]
	callable DCreateFileA(fn as string, access as uint, share as uint, secattr as IntPtr, disp as uint, flags as uint, tpl as IntPtr) as IntPtr
	static def CreateFileAHooker(fn as string, access as uint, share as uint, secattr as IntPtr, disp as uint, flags as uint, tpl as IntPtr) as IntPtr:
		handle = CreateFileA(fn, access, share, secattr, disp, flags, tpl)
		if fn.StartsWith('\\\\?\\hid'):#vid_21a1&pid_0001&mi_01#7&942b1e3&0&0000#{4d1e55b2-f16f-11cf-88cb-001111000030}':
			Handles.Add(handle)
			return handle
		return handle

	[DllImport('Kernel32.dll', CallingConvention: CallingConvention.StdCall, CharSet: CharSet.Ansi)]
	static def CloseHandle(handle as IntPtr) as bool:
		pass
	[UnmanagedFunctionPointer(CallingConvention.StdCall)]
	callable DCloseHandle(handle as IntPtr) as bool
	static def CloseHandleHooker(handle as IntPtr) as bool:
		return CloseHandle(handle)
	
	[DllImport('Kernel32.dll', CallingConvention: CallingConvention.StdCall, CharSet: CharSet.Ansi)]
	static def ReadFile(handle as IntPtr, buf as IntPtr, toRead as int, read as IntPtr, olapped as IntPtr) as bool:
		pass
	[UnmanagedFunctionPointer(CallingConvention.StdCall)]
	callable DReadFile(handle as IntPtr, buf as IntPtr, toRead as int, read as IntPtr, olapped as IntPtr) as bool
	static def ReadFileHooker(handle as IntPtr, buf as IntPtr, toRead as int, read as IntPtr, olapped as IntPtr) as bool:
		if handle in Handles:
			handle = RPipe
		return ReadFile(handle, buf, toRead, read, olapped)
	
	def Run(context as RemoteHooking.IContext, _channel as string):
		App.Log('Started')
		
		wpipe as IntPtr
		if not CreatePipe(RPipe, wpipe, IntPtr(0), 16*33):
			App.Log('Pipe creation failed')
			return
		
		App.Log('Pipe created')
		CreateFileAHook = LocalHook.Create(
				LocalHook.GetProcAddress('Kernel32.dll', 'CreateFileA'), 
				DCreateFileA(CreateFileAHooker), 
				self
			)
		CreateFileAHook.ThreadACL.SetExclusiveACL((0, ))
		CloseHandleHook = LocalHook.Create(
				LocalHook.GetProcAddress('Kernel32.dll', 'CloseHandle'), 
				DCloseHandle(CloseHandleHooker), 
				self
			)
		CloseHandleHook.ThreadACL.SetExclusiveACL((0, ))
		ReadFileHook = LocalHook.Create(
				LocalHook.GetProcAddress('Kernel32.dll', 'ReadFile'), 
				DReadFile(ReadFileHooker), 
				self
			)
		ReadFileHook.ThreadACL.SetExclusiveACL((0, ))
		RemoteHooking.WakeUpProcess()
		App.Log('Woken up')
		
		stream = FileStream(wpipe, FileAccess.Write)
		while true:
			packet = App.NextPacket()
			stream.Write(packet, 0, packet.Length)
			Thread.Sleep(1)
