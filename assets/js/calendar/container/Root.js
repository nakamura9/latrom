import React, {Component} from 'react';
import Month from '../components/Month/Month';
import WeekView from '../components/Week/WeekView';
import DayView from '../components/Day/DayView';
import axios from 'axios';
import {BrowserRouter as Router, Route, Link} from 'react-router-dom';

/*
<div>
                <Link to="previous"><i className="fa fas-chevron-left"></i></Link>
                <Link to="next"><i className="fa fas-chevron-right"></i></Link>
            </div>
*/
export default class CalendarRouter extends Component{
    state = {
        year: 2018,
        month: 1,
        day: 1
    }
    componentDidMount(){
        const today = new Date();
        this.setState({
            day: today.getDate(),
            month: today.getMonth() + 1,
            year: today.getFullYear()
        }, () => {
            console.log(this.state);
        });
    }
    render(){
        return(
            <Router>
                <div>
                    <nav>
                        <ul>
                            <li>
                                <Link to={`/calendar/month/${this.state.year}/${this.state.month}`}>Month</Link>
                                <Link to={`/calendar/week/${this.state.year}/${this.state.month}/${this.state.day}`}>Week</Link>
                                <Link to={`/calendar/day/${this.state.year}/${this.state.month}/${this.state.day}`}>Day</Link>
                            </li>
                        </ul>
                    </nav>
                    <Route path="/calendar/month/:year/:month" component={Month} />
                    <Route path="/calendar/week/:year/:week" component={WeekView}/>
                    <Route path="/calendar/day/:year/:month/:day" component={DayView}/>
                </div>
            </Router>
        )
    }
    
}
/*
export default class CalendarRoot extends Component{
    setData = () =>{
        axios.get('/planner/api/calendar',{
            params: {
                view: this.state.nextView,
                current: this.state.current
            }
        }).then(res =>{
            console.log(res.data);
            this.setState({
                data: res.data.data,
                period: res.data.period,
                view:this.state.nextView
            });
        });
    }

} */