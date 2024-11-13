####Mayan-Gregorian converter
##name of compilation: mayan
##contains several converter functions: see "starter help" for more
##rename functions?

####Create a starter help function
help=function(x="mayan"){
    if(x=="long.count"){ ##function 1
        ans=cat("The function 'long.count' converts a Gregorian date to the long count.\nThe default value is the current date.\n     Example: long.count('2/4/1998')
                \nTo calculate BC dates, add a minus sign in front of the year.\n     Example: long.count('2/4/-1998')")
    }else if(x=="get.greg"){ ##function 2
        ans=cat("The function 'get.greg' converts a long count to a corresponding Gregorian date. There is no default value.
                \nFurther elaboration:\nThe long count structure is baktun.katun.tun.winal.kin.\nThe range of numbers accepted are as follows:\n    katun (0-19), tun (0-19), winal (0-17), kin (0-19).\n    Input of numbers outside these accepted ranges will still generate a Gregorian date,\n    but we cannot guarantee the generated date to be correct.
                \nExample: get.greg('10.3.15.2.17')")
    }else if(x=="show.tzolkin"){ ##function 3
        ans=cat("The function 'show.tzolkin' produces the names of the 20 cholq'ij days.\n    The default value of 0 will present the entire table.\n    Input of any number from 1 to 20 will produce the cholq'ij day of the number.
                \nExample: show.tzolkin(5)")
    }else if(x=="tzol2greg"){ ##function 4
        ans=cat("The function 'tzol2greg' produces 5 Gregorian dates of the specified cholq'ij day. There is no default value.
                \nExample: tzol2greg(13)")
    }else{
        ans=cat("This compilation has several functions to convert between Gregorian dates and the Mayan long count.
                \nlong.count: converts a Gregorian date to the long count.\nget.greg: converts a long count day to its Gregorian date.\nshow.tzolkin: checks the names of the 20 cholq'ij days.\ntzol2greg: produces 5 Gregorian dates for the specified cholq'ij day.
                \nFor details of each function, type 'help('name_of_function')'.")
    }
    return(ans)
}

####Create reference tables for general use
cycle.dur=144000 ##each baktun lasts for 144,000 days
ad1=as.Date("0000-01-01")
ad2=as.Date("0001-01-01")

##Table 1: Baktuns that correspond to AD dates
baktun.nr=c(8:13)
r.baktun.dt=as.Date(c("0041-09-05", "0435-12-09", "0830-03-13", "1224-06-15", "1618-09-18", "2012-12-21"))
tzol.nr=c(9:4) ##cholq'ij number
baktun.tab=data.frame(baktun.nr, r.baktun.dt, tzol.nr)

##Table 2: Baktuns that correspond to BC dates
bc.baktun.nr=c(0:7)
bc.baktun.diff=c(8:1) ##how many baktuns away from baktun 8 (the first baktun with an AD date)
tzol.nr=c(3:10)
bc.baktun.tab=data.frame(bc.baktun.nr, bc.baktun.diff, tzol.nr)
##Unable to add formatted BC dates, hence, need to get R to produce them through calculations
for(i in 1:nrow(bc.baktun.tab)){ ##how many days away from the AD date of baktun 8
    bc.baktun.tab$bc.day.diff[i]=baktun.tab$r.baktun.dt[1]-(cycle.dur*bc.baktun.tab$bc.baktun.diff[i])
}
##Correct the discrepancy between R and gregorian BC dates:
##AD0 doesn't exist (i.e., before AD1 is BC1, not AD0) but it exists in R (i.e., 0000-01-01 is actually BC1)
bc.baktun.tab$bc.day.diff.corr=ifelse(bc.baktun.tab$bc.baktun.nr %in% c(4, 6), ##these two baktuns fall on leap years
                                      bc.baktun.tab$bc.day.diff-366, bc.baktun.tab$bc.day.diff-365)
bc.baktun.tab$bc.r.baktun.dt=as.Date(bc.baktun.tab$bc.day.diff.corr, origin="1970-01-01")
bc.baktun.tab$bc.day.diff=NULL
bc.baktun.tab$bc.day.diff.corr=NULL

##Table 3: 20 Kin and the corresponding cholq'ij names
num=0:19 ##instead of 1:20, to match kin
kiche=c("Ajpu'", ##0 kin = 20 cholq'ij
        "Imox", "Iq'", "Aq'ab'al", "K'at",
        "Kan", "Kame", "Kej", "Q'anil",
        "Toj", "Tz'i'", "B'atz'", "E",
        "Aj", "I'x", "Tz'ikin", "Ajmaq",
        "No'j", "Tijax", "Kawoq"
)
yucatec=c("Ahau",
            "Imix", "Ik", "Akbal", "Kan",
            "Chicchan", "Cimi", "Manik", "Lamat",
            "Muluc", "Oc", "Chuen", "Eb",
            "Ben", "Ix", "Men", "Cib",
            "Caban", "Etznab", "Cauac")
corners=c("south (yellow)", "east (red)", "north (white)", "west (black)")
corners=rep(corners, times=5)
representation=c("sun",
                 "water", "wind", "cave/night", "corn/net",
                 "snake", "death", "deer", "corn reproduction",
                 "sacrifising blood", "authority/wolf", "marriage/monkey", "walking",
                 "family construction", "jaguar", "eagle", "vulture",
                 "earthquake", "storm preparation", "storm")
tzol.tab=data.frame(num, kiche, yucatec, corners, representation)

####Create a vector of fun facts


#### FUNCTION 1 ####
####Converts a gregorian date to the corresponding long count
##default value is the current date
##also produces the cholq'ij day
long.count=function(test=Sys.Date()){
    ##Check whether the test date (i.e., the input date) is AD or BC
    check=grepl("-", test)
    era=ifelse((test!=as.character(Sys.Date()) & check==TRUE), "BC", "AD")

    ####(1)Identify the baktun
    ##for input dates that falls in the AD era
    if(era=="AD"){
        r.test=as.Date(test, format="%d/%m/%Y")
        ##for baktun 7, which is a BC date
        if(r.test<r.baktun.dt[1]){
            nr=7
            dur1=as.numeric(ad1-bc.baktun.tab$bc.r.baktun.dt[8]+1) ##days passed from baktun 7 till the end of BC
            dur2=as.numeric(r.test-ad2) ##days passed from the start of AD till the input date
            duration=dur1+dur2
        ##for baktuns listed in the AD table
        }else if(r.test>r.baktun.dt[1] & r.test<(r.baktun.dt[6]+cycle.dur)){
            for(i in 1:nrow(baktun.tab)){
                baktun.tab$duration[i]=as.numeric(r.test)-as.numeric(baktun.tab$r.baktun.dt[i])
            }
            nr=baktun.tab$baktun.nr[baktun.tab$duration<cycle.dur & baktun.tab$duration>=0]
            duration=baktun.tab$duration[baktun.tab$duration<cycle.dur & baktun.tab$duration>=0]
        ##for future baktuns not in the AD table
        }else if(r.test>(r.baktun.dt[6]+cycle.dur)){
            x=as.numeric(r.test-r.baktun.dt[6])%/%cycle.dur
            nr=13+x
            r.dt=r.baktun.dt[6]+(x*cycle.dur)
            duration=as.numeric(r.test-r.dt)
        }
    ##for baktuns of the BC era
    }else if(era=="BC"){
        ##get a formatted input date
        test=gsub("-", "", test) ##the AD version of the input date
        ad.r.test=as.Date(test, format="%d/%m/%Y") ##format "AD date"
        dur=as.numeric(ad.r.test-ad2)
        bc.r.test=ad1-dur
        ##need to correct the estimated BC date
        r.y=as.Date(substr(bc.r.test, 2, 11), format="%Y-%m-%d")
        off=as.numeric(ad.r.test-r.y) ##how many days off are we from the input date
        bc.r.test=bc.r.test+off
        ##get the right baktun and the number of days lapsed
        for(i in 1:nrow(bc.baktun.tab)){
            bc.baktun.tab$duration[i]=(bc.baktun.tab$bc.r.baktun.dt[i]-bc.r.test)*-1
        }
        bc.baktun.tab$duration=ifelse(bc.baktun.tab$bc.baktun.nr %in% c(0, 1, 5, 7),
                            bc.baktun.tab$duration, bc.baktun.tab$duration-1)
        nr=bc.baktun.tab$bc.baktun.nr[bc.baktun.tab$duration<cycle.dur & bc.baktun.tab$duration>=0]
        duration=as.numeric(bc.baktun.tab$duration[bc.baktun.tab$duration<cycle.dur & bc.baktun.tab$duration>=0])
    }

    ####(2)Calculate the rest of the long count
    baktun=nr
    katun=duration%/%7200
    tun=(duration-(katun*7200))%/%360
    winal=(duration-(katun*7200)-(tun*360))%/%20
    kin=duration%%20

    ####(3)Get the Cholq'ij day
    ##extract the name
    tzol.k=ifelse(nr==0, "-", tzol.tab$kiche[tzol.tab$num==kin])
    tzol.y=ifelse(nr==0, "-", tzol.tab$yucatec[tzol.tab$num==kin])
    ##anchor cholq'ij numbers with those in the baktun table
    tzol.bk=baktun.tab$tzol.nr[baktun.tab$baktun.nr==nr]
    tzol.bk=ifelse(nr>13, tzol.nr[6]-x, tzol.bk) ##for future baktun
    tzol.num=(tzol.bk+duration)%%13
    tzol.num=ifelse(nr==0, "",
                    ifelse(tzol.num==0, 13, tzol.num))
    ##combine the cholq'ij number and name
    tzol.k=paste(tzol.num, tzol.k, sep=" ")
    tzol.y=paste(tzol.num, tzol.y, sep=" ")

    ####(4)Print output
    long=paste0(baktun, ".", katun, ".", tun, ".", winal, ".", kin)
    mes=ifelse(nr<8, "Our calculation for the BC era is still in progress.",
               "Thank you for using the converter.")
    variable=c("Gregorian date:", "Long count:", "Cholq'ij (K'iche'):", "Tzolk'in (Yucatec):", "Message:") ##column 1 of output table
    ##if check==TRUE, need to add BC in output
    test=ifelse(era=="AD", as.character(r.test), as.character(ad.r.test))
    test=paste(test, era, sep=" ")
    output=c(test, long, tzol.k, tzol.y, mes) ##column 2 of output table
    tab=data.frame(variable, output)
    return(tab)
}

#### FUNCTION 2 ####
####Converts a long count to the corresponding gregorian date
##no default value
##also produces the cholq'ij day
get.greg=function(long){
    ##extract number of days passed
    r.long=as.numeric(unlist(strsplit(long, split="\\.")))
    passed=r.long[5]+(r.long[4]*20)+(r.long[3]*360)+(r.long[2]*7200) ##kin+winal+tun+katun
    ##get the baktun's starting greg year and add the days
    start.yr=baktun.tab$r.baktun.dt[baktun.tab$baktun.nr==r.long[1]]
    greg.date=as.Date((as.numeric(start.yr)+passed), origin="1970-01-01")
    ##provide cholq'ij name
    tzol.k=tzol.tab$kiche[tzol.tab$num==r.long[5]]
    tzol.y=tzol.tab$yucatec[tzol.tab$num==r.long[5]]
    ##get cholq'ij date
    nr=r.long[1]
    tzol.bk=baktun.tab$tzol.nr[baktun.tab$baktun.nr==r.long[1]]
    tzol.bk=ifelse(nr>13, tzol.nr[6]-x, tzol.bk)
    tzol.num=(tzol.bk+passed)%%13
    tzol.num=ifelse(nr==0, "",
                ifelse(tzol.num==0, 13, tzol.num))
    tzol.k=paste(tzol.num, tzol.k, sep=" ")
    tzol.y=paste(tzol.num, tzol.y, sep=" ")
    ##print output
    variable=c("Long count:", "Gregorian date:", "Cholq'ij (K'iche'):", "Tzolk'in (Yucatec):")
    output=c(long, as.character(greg.date), tzol.k, tzol.y)
    tab=data.frame(variable, output)
    return(tab)
}

#### FUNCTION 3 ####
####Produces the corresponding cholq'ij day for numbers 1-20
##Given a default value of 0, which will produce the entire table
show.tzolkin=function(nr=0){
    message="Please enter a number from 1 to 20."
    if(nr==0){
        return(tzol.tab)
    }else if(nr %in% 1:20){
        tzol.nr=ifelse(nr==20, 0, nr)
        tzol.k=tzol.tab$kiche[tzol.tab$num==tzol.nr]
        tzol.y=tzol.tab$yucatec[tzol.tab$num==tzol.nr]
        repre=tzol.tab$representation[tzol.tab$num==tzol.nr]
        loca=tzol.tab$corners[tzol.tab$num==tzol.nr]
        ans=paste(nr, "=", tzol.k, "(K'iche') or", tzol.y, "(Yucatec)")
        variable=c("Answer:", "Representation:", "Location:")
        output=c(ans, repre, loca)
        tab=data.frame(variable, output)
        return(tab)
    }else{
        return(message)
    }
}

#### FUNCTION 4 ####
####Generates 5 gregorian dates around the current date for the given cholq'ij day number
##no default value
tzol2greg=function(nr){
    nr=ifelse(nr==20, 0, nr)
    message="Please enter a number from 1 to 20."
    if(nr %in% 0:19){
        tzol.k=tzol.tab$kiche[tzol.tab$num==nr]
        tzol.y=tzol.tab$yucatec[tzol.tab$num==nr]
        ##get today's cholq'ij day
        today=Sys.Date()
        duration=as.numeric(today)-as.numeric(baktun.tab$r.baktun.dt[6])
        kin=duration%%20
        ##calculate the difference between the two tzolkins
        diff=kin-nr
        day3=as.Date((as.numeric(today)-diff), origin="1970-01-01")
        day1=as.Date((as.numeric(day3)-40), origin="1970-01-01")
        day2=as.Date((as.numeric(day3)-20), origin="1970-01-01")
        day4=as.Date((as.numeric(day3)+20), origin="1970-01-01")
        day5=as.Date((as.numeric(day3)+40), origin="1970-01-01")
        ##print output
        variable=c("K'iche' name:", "Yucatec name:", "Date 1:", "Date 2:", "Date 3:", "Date 4:", "Date 5:")
        output=c(tzol.k, tzol.y, as.character(day1), as.character(day2), as.character(day3), as.character(day4), as.character(day5))
        tab=data.frame(variable, output)
        return(tab)
    }else{
        return(message)
    }
}
