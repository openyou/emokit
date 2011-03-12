# The name of the project is "LIBORO". CMakeLists files in this project can
# refer to the root source directory of the project as ${LIBORO_SOURCE_DIR} and
# to the root binary directory of the project as ${LIBORO_BINARY_DIR}.
cmake_minimum_required (VERSION 2.6)
PROJECT(libepoc)

#set(LIBS mcrypt)

SET(BUILD_SHARED_LIBS true)

LIST(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR})

FIND_PACKAGE(Mcrypt REQUIRED)

IF(WIN32)
  SET(WDK_PATH CACHE PATH "Path to WDK Installation")
  INCLUDE_DIRECTORIES(${WDK_PATH}/inc/api ${WDK_PATH}/inc/crt ${WDK_PATH}/inc)
  LINK_DIRECTORIES(${WDK_PATH}/lib/wxp/i386)
  LIST(APPEND LIBEPOC_REQUIRED_LIBS hid setupapi)
ELSEIF(UNIX)
  FIND_PACKAGE(libusb-1.0 REQUIRED)
  IF(LIBUSB_1_FOUND)
    INCLUDE_DIRECTORIES(${LIBUSB_1_INCLUDE_DIRS})
    LIST(APPEND LIBEPOC_REQUIRED_LIBS ${LIBUSB_1_LIBRARIES})
  ENDIF(LIBUSB_1_FOUND)
ENDIF(WIN32)

SET(LIBS ${Mcrypt_LIBS} ${LIBUSB_1_LIBRARIES})

MESSAGE(STATUS ${LIBS})
include_directories(${libepoc_SOURCE_DIR}/include /usr/local/include)
LINK_DIRECTORIES(/usr/local/lib)
set(LIBEPOC_HEADERS include/libepoc.h)

##########################################
##              libepoc                ###
##########################################

# Create a library called "libepoc"

ADD_LIBRARY (epoc STATIC src/epoc.c src/epoc_libusb.c) 

target_link_libraries (epoc ${LIBS}) 

INSTALL (TARGETS epoc
	LIBRARY DESTINATION lib
	ARCHIVE DESTINATION lib
)

INSTALL(FILES
	${LIBEPOC_HEADERS}
	DESTINATION include/libepoc
)

##################################################
#                epoc daemon                   #
##################################################

add_executable (epocd src/epocd.c)

target_link_libraries (epocd epoc ${LIBS}) 

SET_TARGET_PROPERTIES(epocd PROPERTIES
	INSTALL_RPATH_USE_LINK_PATH TRUE
	INSTALL_RPATH ${CMAKE_INSTALL_PREFIX}/lib
	BUILD_WITH_INSTALL_RPATH TRUE )

INSTALL (TARGETS epocd
	RUNTIME DESTINATION bin
)

##########################################
##       PKGCONFIG file                ###
##########################################

IF   (EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/libepoc.pc.in")
    MESSAGE(STATUS "configured ${CMAKE_CURRENT_SOURCE_DIR}/libepoc.pc.in --> ${CMAKE_CURRENT_BINARY_DIR}/libepoc.pc")
    CONFIGURE_FILE(${CMAKE_CURRENT_SOURCE_DIR}/libepoc.pc.in 
      ${CMAKE_CURRENT_BINARY_DIR}/libepoc.pc
      @ONLY )

	INSTALL(FILES
		${CMAKE_CURRENT_BINARY_DIR}/libepoc.pc
		DESTINATION lib/pkgconfig
	)
ENDIF(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/libepoc.pc.in")

