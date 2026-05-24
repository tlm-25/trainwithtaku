function SourcesDisplayContent(props) {

    const {sourcesForCurrentMessage,handleCloseModal} = props

    if (!sourcesForCurrentMessage || typeof sourcesForCurrentMessage !== 'string') {

        return <div className="sources-content"><p>No sources available.</p></div>

    }

    // split the sources for current message into array of inidividual sources using "Source: N" as the delimiter
    const individualSourcesArray = sourcesForCurrentMessage.split(/Source \d+:/).filter(source => source.trim() !== '');




    return (
        <>

        <div className="sources-content">
            <div className='top-of-popup'> <h2 className="popup-title-text">Sources</h2><h3><button onClick={handleCloseModal}>&times;</button></h3></div>
            {individualSourcesArray.length === 0 ? (
                <p>No sources available.</p>
            ) : individualSourcesArray.map((source,index)=>{

                return (
                    <div className="individual-source-block" key={index}>
                        <h4 className="source-name">Source {index+1}</h4>
                        <p className="source-content">{source.trim()}</p>
                    </div>
                )


            })}



        </div>


        
        
        
        </>
    )
}

export default SourcesDisplayContent;