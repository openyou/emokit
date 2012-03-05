##################################################
#                epoc daemon                   #
##################################################

add_executable (emokitd emokitd.c)
ADD_DEPENDENCIES(emokitd emokit)
target_link_libraries (emokitd emokit ${LIBS})

SET_TARGET_PROPERTIES(emokitd PROPERTIES
	INSTALL_RPATH_USE_LINK_PATH TRUE
	INSTALL_RPATH ${CMAKE_INSTALL_PREFIX}/lib
	BUILD_WITH_INSTALL_RPATH TRUE )

INSTALL (TARGETS emokitd
	RUNTIME DESTINATION bin
)

