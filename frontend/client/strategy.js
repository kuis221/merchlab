import React from 'react';
import ReactDOM from 'react-dom';
import TemplateViewer from './components/TemplateViewer.jsx';
import ScheduleViewer from './components/ScheduleViewer.jsx';
import RepriceReportsList from './components/RepriceReportsList.jsx';


ReactDOM.render(<TemplateViewer />, document.getElementById('template-viewer'));
ReactDOM.render(<ScheduleViewer />, document.getElementById('schedule-viewer'));
ReactDOM.render(<RepriceReportsList />, document.getElementById('reprice-reports-list'));
