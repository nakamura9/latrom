import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import ShiftSchedule from './manufacturing/shifts/container/root';
const scheduleTable = document.getElementById('schedule-table');

if(scheduleTable){
    ReactDOM.render(<ShiftSchedule />, scheduleTable);
}