
import ArticleCard from "./ArticleCard";
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
            <ArticleCard imageSource={'/twt-logo.png'} articleHeadline={dummyArticleHeadline} articleContentSample={articleContentSample} />
            <ArticleCard imageSource={'/twt-logo.png'} articleHeadline={dummyArticleHeadline} articleContentSample={articleContentSample} />
            <ArticleCard imageSource={'/twt-logo.png'} articleHeadline={dummyArticleHeadline} articleContentSample={articleContentSample} />
            <ArticleCard imageSource={'/twt-logo.png'} articleHeadline={dummyArticleHeadline} articleContentSample={articleContentSample} />
            <ArticleCard imageSource={'/twt-logo.png'} articleHeadline={dummyArticleHeadline} articleContentSample={articleContentSample} />
            <ArticleCard imageSource={'/twt-logo.png'} articleHeadline={dummyArticleHeadline} articleContentSample={articleContentSample} />
            <ArticleCard imageSource={'/twt-logo.png'} articleHeadline={dummyArticleHeadline} articleContentSample={articleContentSample} />
            <ArticleCard imageSource={'/twt-logo.png'} articleHeadline={dummyArticleHeadline} articleContentSample={articleContentSample} />
            <ArticleCard imageSource={'/twt-logo.png'} articleHeadline={dummyArticleHeadline} articleContentSample={articleContentSample} />
            <ArticleCard imageSource={'/twt-logo.png'} articleHeadline={dummyArticleHeadline} articleContentSample={articleContentSample} />



        </div>

        </>
    )





}

export default ArticleSearchCardContainer;