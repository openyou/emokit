##################################################
# epoc contact #
##################################################

add_executable (contact contact.c)
ADD_DEPENDENCIES(contact emokit)
target_link_libraries (contact emokit ${LIBS})

SET_TARGET_PROPERTIES(contact PROPERTIES
INSTALL_RPATH_USE_LINK_PATH TRUE
INSTALL_RPATH ${CMAKE_INSTALL_PREFIX}/lib
BUILD_WITH_INSTALL_RPATH TRUE )

INSTALL (TARGETS contact
RUNTIME DESTINATION bin
)
