>>

# create socket bind and listen  to port 1025 ip address 0
> # case byte = 0
>+ # lower byte of port
>++++ # upper byte of port
<<<@

# accept
<+ # case byte = 1
<@

# copy client sd
>>[-]<<
[>>+<<-]

# put "A" at idx 0
>[-]++++++
[<++++++++++>-]
<+++++

# write "A"
>+++ # case byte = 3
<@

# write newline
[-]++++++++++
@
