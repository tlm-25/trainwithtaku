
import { useState, useEffect } from "react";
import ArticleCard from "./ArticleCard";
import { BASE_URL } from "../../api";

function ArticleSearchCardContainer (){
    /**
     *Placeholder for article headlien
     */
    const dummyArticleHeadline = "HEADLINE"
    const dummyImageSource = "SOURCE"
    const articleContentSample = "This is the sample of an article that has been written about fitness..."
    const [articles, setArticles] = useState([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const limit = 10;
    
    useEffect(() => {
        async function fetchArticles() {
            try {
                const response = await fetch(`${BASE_URL}/api/blogs?page=${page}&limit=${limit}`);
                const data = await response.json();
                setArticles(data.blogs);
                setTotalPages(data.total_pages);
            } catch (error) {
                console.error("Failed to fetch articles", error);
            }
        }
        fetchArticles();
    }, [page]);


    return (
        <>
            <div className="article-card-container">
                {articles.map((article) => (
                    <ArticleCard
                        key={article.article_id}
                        imageSource={article.headline_image_url}
                        articleHeadline={article.title}
                        articleContentSample={article.article_text.slice(0, 100)}
                    />
                ))}
            </div>

            <div className="pagination-controls">
                <button disabled={page <= 1} onClick={() => setPage(p => p - 1)}>Previous</button>
                <span>Page {page} of {totalPages}</span>
                <button disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>Next</button>
            </div>
        </>
    );
}


export default ArticleSearchCardContainer;