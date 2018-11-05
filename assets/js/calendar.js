import React from 'react';
import ReactDOM from 'react-dom';
import CalendarRouter from './calendar/container/Root';
import TreeSelectWidget from '../js/src/tree_select_widget';
import ParticipantSelectWidget from '../js/calendar/components/ParticipantSelect/select';


const calendar = document.getElementById('calendar-root');
const participantSelect = document.getElementById('participant-select');
if(calendar){
    ReactDOM.render(<CalendarRouter />, calendar);
}else if(participantSelect){
    ReactDOM.render(<ParticipantSelectWidget />, participantSelect);
}

