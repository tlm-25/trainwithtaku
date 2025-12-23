import Navigation from "./Navigation";


function Layout(props){

    const {children} = props;

    const header = (
        <Navigation/>
    )

    const footer = (
        <div className="webpage-footer">
            <div>trainwithtaku@gmail.com</div>
            <div>@trainwithtaku</div>
            <div> Youtube: Train with Taku </div>


        </div>
    )

    return(
        <>

        {header}

        <main>
            {children}
        </main>

        {footer}

        </>
    );
}






export default Layout;