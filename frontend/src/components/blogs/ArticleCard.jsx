function ArticleCard(props) {


    const {imageSource, articleHeadline, articleContentSample} = props 


    return (
        <>

            <div className="article-card">
                <img src={imageSource} className="article-card-image"/>
                <div className="article-card-headline-container">
                    <h4>{articleHeadline}</h4>
                </div>
                <p>
                    {articleContentSample}
                    
                </p>


            </div>
        </>
    )
}

export default ArticleCard;