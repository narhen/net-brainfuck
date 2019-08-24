>>

# create socket and bind to port 1025 ip address 0
> # case byte = 0
>+ # lower byte of port
>++++ # upper byte of port
<<<@

# listen
<+ # case byte = 1
<@

# accept
>+ # case byte = 2
<@

# copy client sd
>>[-]<<
[>>+<<-]

# put "A" at idx 0
>[-]++++++
[<++++++++++>-]
<+++++

# write "A"
>++++ # case byte = 4
<@

# write newline
[-]++++++++++
@
