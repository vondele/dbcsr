
set(DBCSR_PROGRAM_SRCS
  dbcsr_example_1.F
  dbcsr_example_2.F
  dbcsr_example_3.F
  )

# register each program source file as executable
foreach (dbcsr_program_src ${DBCSR_PROGRAM_SRCS})
  get_filename_component(dbcsr_program_name ${dbcsr_program_src} NAME_WE)
  add_executable(${dbcsr_program_name} ${dbcsr_program_src})
  target_link_libraries(${dbcsr_program_name} dbcsr)
endforeach ()

if (WITH_C_API)
  add_executable(dbcsr_example_3_cpp dbcsr_example_3.cpp)
  target_link_libraries(dbcsr_example_3_cpp dbcsr_c ${MPI_CXX_LIBRARIES})
  target_compile_features(dbcsr_example_3_cpp PRIVATE cxx_std_14)
  target_compile_options(dbcsr_example_3_cpp PUBLIC ${MPI_CXX_COMPILE_FLAGS})
endif ()
