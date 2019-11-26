function getCalendar(year, month){
    //2d array start from first day 
    var first = new Date(year, month, 1)
    var i;
    var dateArray = [];
    for(i=1;i < 32; i++){
        dateArray.push(new Date(year, month, i))
    }
    return dateArray.filter(function(date){
        return date.getMonth() == first.getMonth()
    })
}

console.log(getCalendar(2019, 10));