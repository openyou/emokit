# The name of the project is "LIBORO". CMakeLists files in this project can
# refer to the root source directory of the project as ${LIBORO_SOURCE_DIR} and
# to the root binary directory of the project as ${LIBORO_BINARY_DIR}.
cmake_minimum_required (VERSION 2.6)
PROJECT(libepoc)

set(LIBS mcrypt)

SET(BUILD_SHARED_LIBS true)

include_directories(${libepoc_SOURCE_DIR}/include)

set(LIBEPOC_HEADERS include/libepoc.h)

##########################################
##              libepoc                ###
##########################################

# Create a library called "libepoc"

ADD_LIBRARY (epoc src/epoc.c) 

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

