##########################################
##              libepoc                ###
##########################################

# Create a library called "libepoc"
IF(WIN32)
  ADD_LIBRARY (emokit STATIC emokit.c emokit_win32.c) 
ELSE()
  ADD_LIBRARY (emokit STATIC emokit.c emokit_libusb.c) 
ENDIF()
target_link_libraries (emokit ${LIBS}) 

INSTALL (TARGETS emokit
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
  )

INSTALL(FILES
  ${LIBEMOKIT_HEADERS}
  DESTINATION include/libemokit
  )
