function SourcesDisplayContent(props) {

    const {sourcesForCurrentMessage,handleCloseModal} = props
    
    //guard clause against incorrect json parsing, or there are no documents retrieved
    if (!Array.isArray(sourcesForCurrentMessage) || sourcesForCurrentMessage.length === 0) {
        return <div className="sources-content"><p>No sources available.</p></div>
    }





    return (
        <div className="sources-content">
            <div className='top-of-popup'>
                <h2 className="popup-title-text">Sources</h2>
                <h3><button onClick={handleCloseModal}>&times;</button></h3>
            </div>
            {sourcesForCurrentMessage.map((source, index) => (
                <div className="individual-source-block" key={index}>
                    <h4 className="source-name">Source {index + 1}</h4>
                    <a href={source.url} target="_blank" rel="noreferrer">{source.url}</a>
                    <br></br>
                    <p className="source-content"><i>"{source.page_content}"</i></p>
                </div>
            ))}
        </div>
    )
}

export default SourcesDisplayContent;