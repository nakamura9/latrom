import React from 'react';
import MiniCalendar from '../components/mini_calendar';
import {BrowserRouter as Router, Route, Link} from 'react-router-dom';
import styles from './sidebar.css';

const sidebar = (props) =>{
    const navHeight = document.getElementById('navbar').offsetHeight;
    const height = document.documentElement.clientHeight - navHeight -2;
    return(
        <div id="sidebar" className={styles.sidebar} style={{height:height}}>
        <a href="/planner/event-create/"
        className="btn btn-primary btn-block"> <i className="fas fa-plus"></i> Create New Event</a>
            <div className="btn-group">            
                <Link className="btn btn-primary" 
                    to={`/calendar/month/${props.calendarState.year}/${props.calendarState.month}`}><i className="fa fas-calendar"></i> Month</Link>
                <Link className="btn btn-primary" 
                    to={`/calendar/week/${props.calendarState.year}/${props.calendarState.month}/${props.calendarState.day}`}>Week</Link>
                <Link className="btn btn-primary" 
                    to={`/calendar/day/${props.calendarState.year}/${props.calendarState.month}/${props.calendarState.day}`}>Day</Link>
            </div>
            <div className="btn-group">
                <button
                    className="btn btn-primary"
                    onClick={props.prevHandler}>
                        <i className="fas fa-arrow-left"></i>
                </button>    
                <button
                    className="btn btn-primary"
                    onClick={props.nextHandler}>
                        <i className="fas fa-arrow-right"></i>
                </button>
            </div>
            <div>
                <MiniCalendar 
                    year={props.calendarState.year}
                    month={props.calendarState.month} />
            </div>
            
        </div>
    );
}

export default sidebar;