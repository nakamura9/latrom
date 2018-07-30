import React, {Component} from 'react';

//day represented by json 
//date: 'string'
//activities []
//activity represented by json 

class Calender extends Component{
    
}

class WeekView extends Component{
    render()
}

class AgendaViewextends Component{
    render()
}

export default class MonthView extends Component{
    render(){

    }
}

class MonthViewCell extends Component{
    render(){
        return(
            <div>
                <div className="dayHeader">
                    <h3 style={{float:'right'}}>{day.day}</h3>
                </div>
                <div className="dayContent">
                    {this.props.day.activities.map((activity, i) =>{
                        return(<ActivityBadge activity={activity}/>)
                    })}
                </div>
                <div className="dayFooter"></div>
            </div>
        );
    }
}

class ActivityBadge extends Component{
    render(){
        return(
            <div>
                Activity Content
            </div>
        );
    }
}

class MonthViewRow extends Component{
    render(){
        return(
            <div>
                {this.state.days.map((day, i) => {
                    <MonthViewCell day={day}/>
                })}
            </div>
            
        );
    }
}