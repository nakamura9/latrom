import React, {Component} from 'react';
import Month from '../components/Month/Month';
import WeekView from '../components/Week/WeekView';
import DayView from '../components/Day/DayView';
import axios from 'axios';
import {BrowserRouter as Router, Route, Link} from 'react-router-dom';
import MiniCalendar from '../components/mini_calendar';

export default class CalendarRouter extends Component{
    state = {
        year: 2018,
        month: 1,
        day: 1,
        nextLink: "",
        prevLink: ""
    }

    nextHandler = () =>{
        this.setLinks()
        window.location.replace(this.state.nextLink);
    }
    prevHandler = () =>{
        this.setLinks()
        window.location.replace(this.state.prevLink);
    }

    componentDidMount(){
        this.setLinks();
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
                <div className="container-fluid">
                <div className="row">
                <div className="col-sm-2" style={{
                    backgroundColor: "#07f"
                }}>
                {/*Side bar */}            
                    <div className="btn-group">            
                        <Link className="btn btn-primary" 
                            to={`/calendar/month/${this.state.year}/${this.state.month}`}><i className="fa fas-calendar"></i> Month</Link>
                        <Link className="btn btn-primary" 
                            to={`/calendar/week/${this.state.year}/${this.state.month}/${this.state.day}`}>Week</Link>
                        <Link className="btn btn-primary" 
                            to={`/calendar/day/${this.state.year}/${this.state.month}/${this.state.day}`}>Day</Link>
                    </div>
                    <div 
                        className="btn-group"
                        style={{
                            "display": "block",
                            "marginTop": "5px"
                        }}>
                        <button
                            className="btn btn-primary"
                            onClick={this.prevHandler}>
                                <i className="fas fa-arrow-left"></i>
                        </button>    
                        <button
                            className="btn btn-primary"
                            onClick={this.nextHandler}>
                                <i className="fas fa-arrow-right"></i>
                        </button>
                    </div>
                    <div>
                        <MiniCalendar 
                            year={this.state.year}
                            month={this.state.month} />
                    </div>   
                    <a 
                        href="/planner/event-create/"
                        className="btn btn-primary">Create New Event</a>    
                </div>
                <div className="col-sm-10" >
                    {/*App */}
                    <Route 
                        path="/calendar/month/:year/:month" 
                        render={(props) => <Month {...props} linkUpdater={this.setLinks}/>} />
                    <Route 
                        path="/calendar/week/:year/:month/:day" 
                        render={(props) => <WeekView {...props} linkUpdater={this.setLinks}/>}/>
                    <Route 
                        path="/calendar/day/:year/:month/:day" 
                        render={(props) => <DayView {...props} linkUpdater={this.setLinks}/>}/>
                </div>
            </div>
                </div>
                
            </Router>
        )
    }
    
}