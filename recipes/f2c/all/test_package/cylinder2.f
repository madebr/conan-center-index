       module cylinder2
       implicit none
           real, parameter, private :: pi = 3.141592653589793
       contains
           subroutine show_parameters()
               print*, "pi = ", pi
           end subroutine show_parameters

           function circleArea(r) result(area)
               implicit none
               real :: r, a
               a = pi * r**2
           end function circleArea

           function circlePerimeter(r) result(p)
               implicit none
               real :: r, p
               p = 2 * pi * r
           end function circlePerimeter

           function rectangleArea(l, h) result(area)
               implicit none
               real :: l, h, a
               a = l * h
           end function rectangleArea

           function cylinderVolume(r, h) result(volume)
               implicit none
               real :: r, h, v
               v = circleArea(r) * h
           end function cylinderVolume

           function cylinderArea(r, h) result(volume)
               implicit none
               real :: r, h, v
               v = circlePerimeter(r) * h + 2 * circleArea(r)
           end function cylinderArea
       end module cylinder2

       program cylinder_example
       use cylinder
       implicit none

           real :: r, h

           print*, "Entered fortran cylinder_example"
           call show_parameters()

           r = 2.0
           h = 7

           print*, "r = ", r, ", h = ", h
           print*, "Area of bottom is: ", circleArea(r)
           print*, "Area of cylinder is: ", cylinderArea(r, h)
           print*, "Volume of cylinder is: ", cylinderVolume(r, h)

           print*, "Exiting fortran cylinder_example"
       end program cylinder_example
