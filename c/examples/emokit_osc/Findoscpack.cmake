# - Find Mcrypt (a cross platform RPC lib/tool)
# This module defines
# Mcrypt_INCLUDE_DIR, where to find Mcrypt headers
# Mcrypt_LIBS, Mcrypt libraries
# Mcrypt_FOUND, If false, do not try to use Mcrypt
 
find_path(oscpack_INCLUDE_DIR oscpack/osc/OscTypes.h PATHS
    /usr/local/include
    /opt/local/include
  )

#find_library can't seem to find a 64-bit binary if the 32-bit isn't there

set(oscpack_LIB_PATHS /usr/local/lib /opt/local/lib /usr/lib64)
find_library(oscpack_LIB NAMES oscpack PATHS ${oscpack_LIB_PATHS})
 
if (oscpack_LIB AND oscpack_INCLUDE_DIR)
  set(oscpack_FOUND TRUE)
  set(oscpack_LIBS ${oscpack_LIB})
else ()
  set(oscpack_FOUND FALSE)
endif ()
 
if (oscpack_FOUND)
  if (NOT oscpack_FIND_QUIETLY)
    message(STATUS "Found oscpack: ${oscpack_LIBS}")
  endif ()
else ()
  if (oscpack_FIND_REQUIRED)
      message(FATAL_ERROR "Could NOT find oscpack library.")
  endif ()
  message(STATUS "oscpack NOT found.")
endif ()
 
mark_as_advanced(
    oscpack_LIB
    oscpack_INCLUDE_DIR
  )
