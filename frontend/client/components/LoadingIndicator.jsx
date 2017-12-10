import React from 'react';

export default class LoadingIndicator extends React.Component {
	render() {
		var loadingText = this.props.loadingText || "Loading... Hang tight!";
		return (
			<div className="text-center">
				<h3 style={ {fontFamily: 'Open Sans', fontWeight:300} }>{loadingText}</h3>
				<br />
				<div className='loader-1' /><br /><br />
			</div>
		)
	}

}