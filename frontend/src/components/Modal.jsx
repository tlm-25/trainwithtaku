import ReactDom from 'react-dom'

export default function Modal (props) {
    const {children,showModal,handleCloseModal} = props
    return ReactDom.createPortal(
        <div className={'modal-container' +(showModal ? " modal-container-active":" ")}>
            <button className='modal-underlay' onClick={handleCloseModal}/>
            <div className='modal-content'>
                {children}
            </div>

        </div>,
        document.getElementById('portal')
    )
}