import React, {Component} from 'react';
import Month from '../components/Month/Month';
import WeekView from '../components/Week/WeekView';
import DayView from '../components/Day/DayView';
import axios from 'axios';

export default class CalendarRoot extends Component{
    state = {
        view: 'month',
        nextView: 'month',
        data: [],
        period: '',
        current: 0
    }
    componentDidMount(){
        this.setData();
    }

    componentDidUpdate(prevProps, prevState){
        if( this.state.nextView !== prevState.nextView || 
            this.state.current !== prevState.current){
                this.setData();
            }
    }
    
    setData = () =>{
        axios.get('/base/api/calendar',{
            params: {
                view: this.state.nextView,
                current: this.state.current
            }
        }).then(res =>{
            this.setState({
                data: res.data.data,
                period: res.data.period,
                view:this.state.nextView
            });
        });
    }

    setCurrent = (val) =>{
        this.setState((prevState) =>{
            return({current: prevState.current + val});
        });
    }
    //change the data based on the changes in state of the 
    // current and the view 
    render(){
        let view = null;
        switch(this.state.view){
            case 'month':
                view=<Month 
                    weeks={this.state.data}
                    period={this.state.period}/>
                break;
            case 'week':
                view = (
                    <WeekView 
                        days={this.state.data}
                        period={this.state.period}/>            
                )
                break;
            case 'day':
                view= <DayView data={this.state.data}/>
                break;
            default:
                view=<h1>Loading View...</h1>

        }
        return(
        <div>
            <h1>Calendar</h1>
            <div>
                <button onClick={() => {this.setState({nextView:'day'})}}>
                    Day
                </button>
                <button onClick={() => {this.setState({nextView:'week'})}}>
                    Week
                </button>
                <button onClick={() => {this.setState({nextView:'month'})}}>
                    Month
                </button>
            </div>
            <div>
                <button onClick={() => {this.setCurrent(-1)}}>Previous</button>
                <button onClick={() => {this.setCurrent(1)}}>Next</button>
            </div>
            {view}
        </div>
        );
    }
}