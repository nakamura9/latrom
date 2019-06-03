import React, {Component} from 'react';
import Month from '../components/Month/Month';
import WeekView from '../components/Week/WeekView';
import DayView from '../components/Day/DayView';
import axios from 'axios';
import {BrowserRouter as Router, Route, Link} from 'react-router-dom';
import Sidebar from '../components/sidebar';

export default class CalendarRouter extends Component{
    state = {
        year: 2018,
        month: 1,
        day: 1,
        nextLink: "",
        prevLink: "",
        windowWidth: 135,
        windowHeight: 95
    }

    nextHandler = () =>{
        this.setLinks();
        window.location.replace(this.state.nextLink);
    }
    prevHandler = () =>{
        this.setLinks();
        window.location.replace(this.state.prevLink);
    }

    componentDidMount(){
        this.setLinks();
        // calculate the cell width
        // get the screen width
        // subtract the sidebar width
        // divide by 7
        // subtract the padding and border widths 
        this.setState({windowWidth: Math.floor(
            ((window.screen.width -250) / 7) - 12)});
        this.setState({windowHeight: 58});

    }

    setLinks = () =>{
        // for setting mini calendar
        const splitURL = window.location.href.split("/");
        const type = splitURL[4];
        // numbered normally
        let dateData = {
            month: splitURL[6],
            year: splitURL[5],
            day: 1
        }
        this.setState(dateData);

        if(type === "month"){
            // month ranges from 0 - 11 
            // url ranges from 1 -12 
            // therefore next month is the same
            let nextDate = new Date(dateData.year, dateData.month, 1);
            //subtract one for the date mode and another one for the deduction
            let prevDate = new Date(dateData.year, dateData.month - 2, 1);

            // add 1 to each month to represent the normal representation of the month
            this.setState({
                prevLink: `/calendar/month/${prevDate.getFullYear()}/${prevDate.getMonth() + 1}`,
                nextLink: `/calendar/month/${nextDate.getFullYear()}/${nextDate.getMonth() + 1}`
            });
            
        }else if(type === "week"){
            dateData['day'] = splitURL[7];

            // subtract 1 from both months to match the js numbering
            let nextDate = new Date(
                dateData.year, 
                dateData.month - 1, 
                dateData.day);
            
            nextDate.setDate(nextDate.getDate() + 7);
            
            let prevDate = new Date(
                dateData.year, 
                dateData.month - 1, 
                dateData.day);
            
            prevDate.setDate(prevDate.getDate() - 7);
            this.setState(dateData);
            // add 1 to the months to match normal month counting
            this.setState({
                prevLink: `/calendar/week/${prevDate.getFullYear()}/${prevDate.getMonth() + 1}/${prevDate.getDate()}`,
                nextLink: `/calendar/week/${nextDate.getFullYear()}/${nextDate.getMonth() + 1}/${nextDate.getDate()}`
            });
        }else{
            dateData['day'] = splitURL[7];

            // subtract 1 from both months to match the js numbering
            let nextDate = new Date(
                dateData.year, 
                dateData.month - 1, 
                dateData.day);
            
            nextDate.setDate(nextDate.getDate() + 1);

            let prevDate = new Date(
                dateData.year, 
                dateData.month - 1, 
                dateData.day);
            
            prevDate.setDate(prevDate.getDate() - 1);

            this.setState(dateData);

            this.setState({
                prevLink: `/calendar/day/${prevDate.getFullYear()}/${prevDate.getMonth() + 1}/${prevDate.getDate()}`,
                nextLink: `/calendar/day/${nextDate.getFullYear()}/${nextDate.getMonth() + 1}/${nextDate.getDate()}`
            });
        }
    }
    

    render(){
        return(
            <Router>
                <div >
                    <Sidebar calendarState={{...this.state}}
                            nextHandler={this.nextHandler}
                            prevHandler={this.prevHandler}/>
                    <div style={{
                        display:'inline-block', 
                        float: 'left', 
                    'width':'500px',
                        clear: 'right'}}>
                        {/*App */}
                        <Route 
                            path="/calendar/month/:year/:month" 
                            render={(props) => 
                                <Month width={this.state.windowWidth} 
                                        height={this.state.windowHeight}
                                        {...props} 
                                        linkUpdater={this.setLinks}/>} />
                        <Route 
                            path="/calendar/week/:year/:month/:day" 
                            render={(props) => <WeekView width={this.state.windowWidth} {...props} linkUpdater={this.setLinks}/>}/>
                        <Route 
                            path="/calendar/day/:year/:month/:day" 
                            render={(props) => <DayView {...props} linkUpdater={this.setLinks}/>}/>
                    </div>
                </div>
            </Router>
        )
    }
    
}