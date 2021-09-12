import React from 'react'





export default (props) => {
    console.log(props)
    return <div className="container mx-auto px-4 sm:px-8">
            <div className="py-0">
                {
                    props.title?<div>
                        <h2 className="text-2xl font-semibold leading-tight">{props.title}</h2>
                    </div>:null
                }
                <div className="-mx-4 sm:-mx-8 px-4 sm:px-8 py-4 overflow-x-auto">
                    <div className="inline-block min-w-full shadow rounded-lg overflow-hidden">
                        <table className="min-w-full leading-normal">
                            <thead>
                                {
                                    props.header.map(v=>
                                        <tr>
                                            {v.map(v=><th
                                                className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                                {v}
                                             </th>)}
                                        </tr>

                                    )
                                }
                            </thead>
                            <tbody>
                                {
                                    props.body.map(v=>
                                        <tr>
                                            {
                                                v instanceof Array?
                                                v.map(v=><td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                                                <p className="text-gray-900 whitespace-no-wrap text-center">
                                                    {v}
                                                    </p>
                                             </td>):v}
                                        </tr>

                                    )
                                }
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
}