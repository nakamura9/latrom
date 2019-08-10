import React from 'react';
import ReactDOM from 'react-dom';
import CalendarRouter from './calendar/container/Root';
import TreeSelectWidget from '../js/src/tree_select_widget';
import ParticipantSelectWidget from '../js/calendar/components/ParticipantSelect/select';
import TimelineWidget from './src/timeline/container/root';


const calendar = document.getElementById('calendar-root');
const timeline = document.getElementById('agenda-timeline');
const participantSelect = document.getElementById('participant-select');
if(calendar){
    ReactDOM.render(<CalendarRouter />, calendar);
}else if(participantSelect){
    ReactDOM.render(<ParticipantSelectWidget />, participantSelect);
}else if(timeline){
    const url = window.location.href;
    const splitURL = url.split('/');
    const tail = splitURL[splitURL.length -1]
    const dataURL = '/planner/api/agenda/' + tail;
    const resProcessor =(res) =>{
        return res.data.map((i) =>({
            timestamp: i.date + ' ' + i.start_time,
            title: i.label,
            id: i.id
        }))
    }
    ReactDOM.render(<TimelineWidget 
                        dataURL={dataURL}
                        resProcessor={resProcessor} />, timeline)
}

