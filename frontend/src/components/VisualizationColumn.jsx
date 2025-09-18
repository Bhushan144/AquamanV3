// src/components/VisualizationColumn.jsx
import React, { useState, useMemo } from 'react';
import Plot from "react-plotly.js";
import 'leaflet/dist/leaflet.css';
import MapView from './MapView';
import { Skeleton } from '@mantine/core';

const VisualizationColumn = ({ messages, isLoading }) => {
  const [showQuery, setShowQuery] = useState(false);

  const latestVizMsg = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      const msg = messages[i];
      if (msg.role === 'assistant' && (msg.geo_data || msg.table_data)) {
        return msg;
      }
    }
    return null;
  }, [messages]);

  return (
    <div className="h-full overflow-y-auto p-6 bg-gray-900 text-white
      [&::-webkit-scrollbar]:w-2
      [&::-webkit-scrollbar-track]:bg-gray-100
      [&::-webkit-scrollbar-thumb]:bg-gray-300
      dark:[&::-webkit-scrollbar-track]:bg-neutral-700
      dark:[&::-webkit-scrollbar-thumb]:bg-neutral-500">
      <h2 className="text-2xl font-bold mb-4 text-center tracking-wide">Data Visualizations</h2>

      {isLoading && (
        <div className="space-y-4">
          <div 
            className="h-7 bg-gray-600 rounded-xl animate-pulse"
            style={{ width: '100%' }}
          />
          <div 
            className="h-96 bg-gray-600 rounded-md animate-pulse"
            style={{ width: '100%' }}
          />
          <div 
            className="h-48 bg-gray-600 rounded-md animate-pulse"
            style={{ width: '100%' }}
          />
        </div>
      )}

      {!isLoading && !latestVizMsg && (
        <div className="text-gray-400">Visual outputs will appear here.</div>
      )}

      {!isLoading && latestVizMsg && (
        <div className="space-y-6">
          {latestVizMsg.geo_data && (
            <div>
              <h3 className="text-xl font-semibold mb-2">Geospatial Visualization</h3>
              <MapView geoData={latestVizMsg.geo_data} />
            </div>
          )}
          {latestVizMsg.table_data && (
            <div>
              <h3 className="text-xl font-semibold mb-2">Tabular Summary</h3>
              <div className="overflow-x-auto rounded-lg border border-gray-700 max-h-96
                [&::-webkit-scrollbar]:w-2
                [&::-webkit-scrollbar-track]:bg-gray-100
                [&::-webkit-scrollbar-thumb]:bg-gray-300
                dark:[&::-webkit-scrollbar-track]:bg-neutral-700
                dark:[&::-webkit-scrollbar-thumb]:bg-neutral-500">
                <table className="w-full text-left text-sm text-gray-300">
                  <thead className="bg-gray-800 text-xs uppercase">
                    <tr>{Object.keys(latestVizMsg.table_data[0]).map(key => <th className="px-4 py-2" key={key}>{key}</th>)}</tr>
                  </thead>
                  <tbody className="bg-gray-700">
                    {latestVizMsg.table_data.map((row, i) => (
                      <tr key={i} className="border-b border-gray-800">
                        {Object.values(row).map((val, j) => <td className="px-4 py-2" key={j}>{String(val)}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          {latestVizMsg.sql_query && (
            <div>
              <h3 className="text-xl font-semibold mb-2">SQL Query</h3>
              <button
                onClick={() => setShowQuery(!showQuery)}
                className="px-3 py-2 text-[15px] rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow hover:from-blue-500 hover:to-indigo-600 focus:outline-none focus:ring-2 focus:ring-blue-400 font-bold tracking-wide"
              >
                {showQuery ? 'Hide' : 'Show'} SQL Query
              </button>
              {showQuery && (
                <pre className="mt-2 bg-gray-800 p-3 rounded-lg text-sm overflow-x-auto
                  [&::-webkit-scrollbar]:w-2
                  [&::-webkit-scrollbar-track]:bg-gray-100
                  [&::-webkit-scrollbar-thumb]:bg-gray-300
                  dark:[&::-webkit-scrollbar-track]:bg-neutral-700
                  dark:[&::-webkit-scrollbar-thumb]:bg-neutral-500">
                  <code>{latestVizMsg.sql_query}</code>
                </pre>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default VisualizationColumn;