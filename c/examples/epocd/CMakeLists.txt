##################################################
#                epoc daemon                   #
##################################################

add_executable (epocd epocd.c)
ADD_DEPENDENCIES(epocd epoc)
target_link_libraries (epocd emokit ${LIBS})

SET_TARGET_PROPERTIES(epocd PROPERTIES
	INSTALL_RPATH_USE_LINK_PATH TRUE
	INSTALL_RPATH ${CMAKE_INSTALL_PREFIX}/lib
	BUILD_WITH_INSTALL_RPATH TRUE )

INSTALL (TARGETS epocd
	RUNTIME DESTINATION bin
)

