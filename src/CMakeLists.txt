##########################################
##              libemokit              ###
##########################################

# Create a library called "libemokit"
ADD_LIBRARY (emokit emokit.c) 
target_link_libraries (emokit ${LIBS}) 

INSTALL (TARGETS emokit
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
  )

IF(BUILD_SHARED_LIBS)
INSTALL (FILES
  ${LIBEMOKIT_HEADERS}
  DESTINATION include/emokit
)
ENDIF()

