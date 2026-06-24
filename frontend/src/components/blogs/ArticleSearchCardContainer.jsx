
import ArticleCard from "./ArticleCard";
import {articles} from "../../dummyData.json"
function ArticleSearchCardContainer (){
    /**
     *Placeholder for article headlien
     */
    const dummyArticleHeadline = "HEADLINE"
    const dummyImageSource = "SOURCE"
    const articleContentSample = "This is the sample of an article that has been written about fitness..."


    return (
        <>
        <div className="article-card-container">


            {articles.map((article,index)=>(
                <ArticleCard key={index}
                            imageSource={article.headline_image_url} 
                            articleHeadline={article.headline} 
                            articleContentSample={article.article_text_sample} />


            ))}
            

        </div>

        </>
    )





}

export default ArticleSearchCardContainer;