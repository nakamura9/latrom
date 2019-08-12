import React, {Component} from 'react';
import {BrowserRouter as Router, Link, Route} from 'react-router-dom';
import MonthView from '../components/month_view';
import YearView from '../components/year_view';


class LeaveCalendar extends Component{
    state = {
        year: 2018,
        month: 1,
        prevLink: "",
        nextLink: ""
    }


    componentDidMount(){
        this.setLinks();
    }

    setLinks = () =>{
        const splitURL = window.location.href.split("/");
        const type = splitURL[5];
        const year = parseInt(splitURL[6]);
        let month = 1;
        if(type === "year"){
            this.setState({
                nextLink: `/employees/leave-calendar/year/${year + 1}`,
                prevLink: `/employees/leave-calendar/year/${year - 1}`
            });        
        }else{
            month=splitURL[7];
            let nextDate = new Date(year, month, 1);
            //subtract one for the date mode and another one for the deduction
            let prevDate = new Date(year, month - 2, 1);
            this.setState({
                prevLink: `/employees/leave-calendar/month/${prevDate.getFullYear()}/${prevDate.getMonth() + 1}`,
                nextLink: `/employees/leave-calendar/month/${nextDate.getFullYear()}/${nextDate.getMonth() + 1}`
            });
        }
        this.setState({
            year: year,
            month: month
        });
    }

    render(){

        const navHeight = document.getElementById('navbar').offsetHeight;
        const height = document.documentElement.clientHeight - navHeight -2;
    
        return(
            <Router >
            <div className="container">
                <div className="row">
                    <div 
                        className="col-sm-2" 
                        style={{
                        backgroundColor: "#07f",
                        height: height + 'px',
                    }}>
                        <div className="btn-group">            
                            <Link className="btn btn-primary" 
                                to={`/employees/leave-calendar/month/${this.state.year}/${this.state.month}`}> Month</Link>
                            <Link className="btn btn-primary" 
                                to={`/employees/leave-calendar/year/${this.state.year}`}>Year</Link>
                        </div>
                        <div 
                            className="btn-group"
                            style={{
                                "display": "block",
                                "marginTop": "5px"
                            }}>
                            <a
                                className="btn btn-primary"
                                href={this.state.prevLink}>
                                    <i className="fas fa-arrow-left"></i>
                            </a>    
                            <a
                                className="btn btn-primary"
                                href={this.state.nextLink}>
                                    <i className="fas fa-arrow-right"></i>
                            </a>
                        </div>
                        <a 
                            className="btn btn-primary"
                            href="/employees/leave-request/">
                            Request leave days
                        </a>
                    </div>
                <div>
                    </div>
                    <div className="col-sm-10" style={{
                        maxHeight: height + 'px',
                        overflowY: 'auto'
                    }}>
                        <Route 
                            path='/employees/leave-calendar/month/:year/:month'
                            render={(props) => <MonthView 
                                {...props}
                                linkUpdater={this.setLinks} />}/>
                        <Route 
                            path='/employees/leave-calendar/year/:year/'
                            render={(props) => <YearView 
                                {...props}
                                innerHeight={height}
                                linkUpdater={this.setLinks} />}/>
                    </div>
                </div>
            
            </div>
            </Router>
        )
    }
}

export default LeaveCalendar;